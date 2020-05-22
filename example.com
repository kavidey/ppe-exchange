server {
  listen 80;
  listen 443;

  server_name 54.188.4.63;

  location / {
      proxy_pass http://localhost:5000/;
  }
}