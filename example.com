server {
  listen 443 ssl;
  listen [::]:443;

  # Update this with the correct domain name
  server_name ppe-exchange.wa.gov;

  # Update these with the correct file locations
  ssl_certificate /home/ubuntu/ppe-exchange_wa_gov.crt;
  ssl_certificate_key /home/ubuntu/ppe-exchange_wa_gov.key;

  location / {
      proxy_pass http://localhost:5000/;
  }
}

server {
       listen 0.0.0.0:80;
       # Update this with the correct domain name like before
       server_name ppe-exchange.wa.gov www.ppe-exchange.wa.gov;
       rewrite ^ https://$host$request_uri? permanent;
}
