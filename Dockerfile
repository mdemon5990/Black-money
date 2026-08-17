FROM php:8.2-apache
RUN a2enmod rewrite
COPY index.php /var/www/html/index.php
RUN mkdir -p /var/www/html/proofs && chown -R www-data:www-data /var/www/html
EXPOSE 80
CMD ["apache2-foreground"]
