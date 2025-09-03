# Use a slim Python 3.12 base image (Debian-based for better compatibility)
FROM python:3.12-slim-bookworm

# Set the working directory
WORKDIR /app

# Install system dependencies (only required packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ cmake make libffi-dev ffmpeg aria2 wget unzip iproute2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Bento4 (only mp4decrypt)
RUN wget -q https://github.com/axiomatic-systems/Bento4/archive/refs/tags/v1.6.0-639.zip \
    && unzip v1.6.0-639.zip \
    && cd Bento4-1.6.0-639 \
    && mkdir cmakebuild && cd cmakebuild \
    && cmake -DCMAKE_BUILD_TYPE=Release .. \
    && make -j$(nproc --all) mp4decrypt \
    && cp mp4decrypt /usr/local/bin/ \
    && cd ../.. \
    && rm -rf Bento4-1.6.0-639 v1.6.0-639.zip

# Copy requirements first to leverage Docker cache
COPY ugbots.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r ugbots.txt \
    && pip install --no-cache-dir "yt-dlp[default]"

# Copy the rest of the application
COPY . .

# Optimize aria2 for max speed
RUN mkdir -p /etc/aria2 \
    && echo "disable-ipv6=true\n" \
         "file-allocation=none\n" \
         "enable-mmap=true\n" \
         "optimize-concurrent-downloads=true\n" \
         "max-concurrent-downloads=20\n" \
         "max-connection-per-server=32\n" \
         "split=32\n" \
         "min-split-size=512K\n" \
         "continue=true\n" \
         "always-resume=true\n" \
         "check-integrity=true\n" \
         "max-overall-upload-limit=1K" > /etc/aria2/aria2.conf

# Add yt-dlp default config for aria2c speed boost
RUN mkdir -p /root/.config/yt-dlp \
    && echo '--downloader aria2c' >> /root/.config/yt-dlp/config \
    && echo '--downloader-args "aria2c:-x 32 -s 32 -k 1M"' >> /root/.config/yt-dlp/config

# Enable BBR (if supported by host kernel)
RUN echo "net.core.rmem_max=67108864" >> /etc/sysctl.conf \
 && echo "net.core.wmem_max=67108864" >> /etc/sysctl.conf \
 && echo "net.ipv4.tcp_rmem=4096 87380 67108864" >> /etc/sysctl.conf \
 && echo "net.ipv4.tcp_wmem=4096 65536 67108864" >> /etc/sysctl.conf \
 && echo "net.ipv4.tcp_congestion_control=bbr" >> /etc/sysctl.conf

# Start processes: Gunicorn + Aria2 + Main Script
CMD gunicorn --bind 0.0.0.0:${PORT:-8000} \
    --workers 1 --threads 2 --timeout 120 app:app & \
    aria2c --enable-rpc --rpc-listen-all --conf-path=/etc/aria2/aria2.conf --daemon=true && \
    python3 main.py
