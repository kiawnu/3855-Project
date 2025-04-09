FROM nginx

COPY ./nginx/nginx.conf /etc/nginx/nginx.conf

COPY . /usr/share/nginx/html

EXPOSE 8300

CMD ["nginx", "-g", "daemon off;"]