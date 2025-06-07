-- Fichier : db/init.sql
-- Ce script est exécuté automatiquement à la création du conteneur MySQL

CREATE DATABASE IF NOT EXISTS valais_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE valais_db;

CREATE TABLE IF NOT EXISTS cities (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  latitude DECIMAL(9,6) NOT NULL,
  longitude DECIMAL(9,6) NOT NULL,
  email VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS themes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS city_themes (
  city_id INT NOT NULL,
  theme_id INT NOT NULL,
  PRIMARY KEY (city_id, theme_id),
  FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (theme_id) REFERENCES themes(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS contents (
  id INT AUTO_INCREMENT PRIMARY KEY,
  theme_id INT NOT NULL,
  title VARCHAR(150) NOT NULL,
  url VARCHAR(255) NOT NULL,
  FOREIGN KEY (theme_id) REFERENCES themes(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS requests (
  id INT AUTO_INCREMENT PRIMARY KEY,
  city_id INT NOT NULL,
  city_themes_id INT NOT NULL,
  request_date DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (city_themes_id) REFERENCES city_themes(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO users (username, password) VALUES
  ('admin', 'scrypt:32768:8:1$k7E37s7odVpQpCaL$97b0704d0b8d521b3c478efec24de723c728d1e819879051c37a461373e640b21aa743b8347dc3b668b02bddd3b28a067cb435b0fa6bf0cfa655d99cb78114f3');

INSERT INTO cities (name, latitude, longitude) VALUES
  ('Sion', 46.230677, 7.358767),
  ('Sierre', 46.291834, 7.532187),
  ('Crans-Montana', 46.309533, 7.477425),
  ('Hérémence', 46.180058, 7.405222),
  ('Bagne', 46.090291, 7.219296),
  ('Brig', 46.315547, 7.987604);

INSERT INTO themes (name) VALUES
  ('Barème impot communal'),
  ('Construction');
  ('Gestion des déchets');

INSERT INTO city_themes (city_id, theme_id) VALUES
  (1, 1),
  (1, 2),
  (2, 1),
  (3, 2);

INSERT INTO contents (theme_id, title, url) VALUES
  (1, 'Guide Touristique Valais PDF', 'https://example.com/valais-tourisme.pdf'),
  (2, 'Programme Culturel Sion PDF', 'https://example.com/sion-culture.pdf');
