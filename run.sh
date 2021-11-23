#!/bin/bash


echo "Starting..."

rm ./database.db
sqlite3 database.db < schema.sql
python main.py

echo "...Done!"