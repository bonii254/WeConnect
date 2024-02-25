-- prepares a MySQL server for the project

CREATE DATABASE IF NOT EXISTS weconnect_dev_db;
CREATE USER IF NOT EXISTS 'weconnect_dev'@'localhost' IDENTIFIED BY 'weconnect_pwd';
GRANT ALL PRIVILEGES ON `weconnect_dev_db`.* TO 'weconnect_dev'@'localhost';
GRANT SELECT ON `performance_schema`.* TO 'weconnect_dev'@'localhost';
FLUSH PRIVILEGES;
