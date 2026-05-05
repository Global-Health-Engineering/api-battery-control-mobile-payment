### ----DEVELEPTER INFOS-------------------------------------------------------------  ###
### This code was developed by:
### Patrick Fässler, ETH Zurich, 2024
### Github: https://github.com/Patrick-Fa-CH
### Email:  faepatr@gmailcom

This project folder is part of the Master Thesis project containing of three main project folder.
The folder PICOONE and PICOTWO are written in micropython and createt for Rasberry Pi Pico. 
The Pico ONE is located in the charger and Pico TWO is located in the battery with a relay.
This only make sense if you use all components and follow the wiring diagramm (contact developper for info).

------This Python project can be split in the following process:-------------------------------------------------
1. Wait for pressing of start button
2. If button pressed, power up and initiate module (insure internet connection)
3. A http POST request is send to the server to get charging status and amount selected energy.
4. If charging granted Pico ONE send command to Pico TWO through UART to close gate. 
5. Pico ONE counts the amount of energy. After achieving selected amount gate gets opened.