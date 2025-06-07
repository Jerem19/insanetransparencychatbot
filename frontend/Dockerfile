# frontend/Dockerfile

FROM nginx:alpine

# Supprimer la configuration par défaut (optionnel)
RUN rm /etc/nginx/conf.d/default.conf

# Copier un fichier de config Nginx personnalisé (si besoin), sinon on se contente du default.
# Ici, on conserve un simple bloc server sur port 80 :
COPY nginx.conf /etc/nginx/conf.d/nginx.conf

# Copier les fichiers statiques dans le dossier servi par Nginx
COPY index.html /usr/share/nginx/html/index.html
COPY style.css /usr/share/nginx/html/style.css
COPY main.js /usr/share/nginx/html/main.js

# Pas d'autres étapes : Nginx sert /usr/share/nginx/html
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
