FROM alpine:3.19

# Install FontForge and Python
RUN apk add --no-cache \
    fontforge \
    python3

# Set working directory
WORKDIR /workspace

# Copy scripts
COPY make-italic.py /workspace/
COPY build.py /workspace/

# Make scripts executable
RUN chmod +x /workspace/make-italic.py /workspace/build.py

# Default command
CMD ["python3", "build.py", "/input", "/output"]
