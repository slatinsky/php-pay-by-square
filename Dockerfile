FROM php:8.3.8-apache
RUN apt-get update && apt-get install -y \
        libfreetype6-dev \
        libjpeg62-turbo-dev \
        libpng-dev \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install -j$(nproc) gd
COPY . /var/www/html/
RUN mkdir -p /var/log/phpqrcode && \
    chown www-data:www-data /var/log/phpqrcode && \
    chmod 755 /var/log/phpqrcode && \
    mkdir -p /tmp/phpqrcode/cache && \
    chown www-data:www-data /tmp/phpqrcode/cache && \
    chmod 755 /tmp/phpqrcode/cache
