# Bimaru Solver Project

## Introduction
This project is developed as part of the Artificial Intelligence course 2022/23. The objective is to create a Python program that solves the Bimaru puzzle.

## Problem Description
The Bimaru game is played on a 10x10 grid representing an ocean area hiding a fleet that the player must find. The fleet consists of one battleship, two cruisers, three destroyers, and four submarines. Ships can be placed horizontally or vertically on the grid but cannot touch each other, even diagonally. The player is given counts of occupied squares in each row and column and several hints regarding the state of individual squares.

## Project Goal
The aim of this project is to develop a Python program that finds a solution for a given Bimaru puzzle instance. The program, contained in `bimaru.py`, reads a puzzle instance from standard input and prints the solution to standard output.

## Usage
```bash
python3 bimaru.py < instance_file
