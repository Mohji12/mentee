-- Add profile_photo_url column to students table for storing Cloudinary photo URLs
ALTER TABLE students
    ADD COLUMN profile_photo_url VARCHAR(500) NULL;
