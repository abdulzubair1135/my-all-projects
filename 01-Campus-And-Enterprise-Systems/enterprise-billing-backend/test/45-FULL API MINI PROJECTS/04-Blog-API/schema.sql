CREATE DATABASE IF NOT EXISTS blog_db;
USE blog_db;

CREATE TABLE IF NOT EXISTS posts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  slug VARCHAR(200) NOT NULL UNIQUE,
  content TEXT NOT NULL,
  author_name VARCHAR(100) NOT NULL,
  status ENUM('draft', 'published') DEFAULT 'draft',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO posts (title, slug, content, author_name, status) VALUES
('Getting Started with Node.js', 'getting-started-with-nodejs', 'Node.js is a powerful JavaScript runtime environment...', 'John Doe', 'published'),
('Mastering Express.js Routing', 'mastering-expressjs-routing', 'Learn how to build scalable routes using Express Router...', 'Jane Smith', 'published');
