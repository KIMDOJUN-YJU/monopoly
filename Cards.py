# This is a dictionary containing the stats of every card in mononpoly
# The meanings of the values are determined by their index and as follows:
# [0]: Tuple of the coordinates where piece will be placed when on property
# [1]: Name of the property
# [2]: Property type
# [3]: Price of properties
# [4]: List of rent prices in ascending order (depends on houses)
# [5]: Mortgage Value
# [6]: Price to build each house
# [7]: Number of houses on the property
# [8]: Building code

# Note: Only properties have index 4-7, because they only apply to that type

# Position Variables

botY = 700
topY = 16
leftX = 27
rightX = 720
mnX = 118
mnY = 118
#botY-mnY*3
cards = {

"Taiwan": [(rightX-mnX, botY), "Taiwan", "property", 60, [2, 10, 30, 90, 160, 250], 30, 50, 0, "brown"],
"Philippines": [(rightX-mnX*2, botY), "Philippines", "property", 60, [4, 20, 60, 180, 320, 450], 30, 50, 0, "brown"],
"China": [(rightX-mnX*3, botY), "China", "property", 60, [6, 30, 90, 270, 400, 550], 50, 70, 0, "brown"],
"Singapore": [(rightX-mnX*4, botY), "Singapore", "property", 100, [6, 30, 90, 270, 400, 550], 50, 70, 0, "sky"],
"Turkey": [(rightX-mnX*5, botY), "Turkey", "property", 100, [8, 40, 100, 300, 450, 600], 50, 70, 0, "sky"],
"Egypt": [(leftX, botY), "Egypt", "property", 200, [16, 80, 220, 600, 800, 100], 100, 150, 0, "sky"],
"Greece": [(leftX, botY-mnY), "Greece", "property", 140, [10, 50, 150, 450, 625, 750], 70, 100, 0, "orange"],
"Denmark": [(leftX, botY-mnY*2), "Denmark", "property", 140, [10, 50, 150, 450, 625, 750], 70, 100, 0, "orange"],
"Sweden": [(leftX, botY-mnY*3), "Sweden", "property", 140, [12, 60, 180, 500, 700, 900], 70, 100, 0, "orange"],
"Suisse": [(leftX, botY-mnY*4), "Suisse", "property", 180, [14, 70, 200, 550, 750, 950], 90, 120, 0, "blue"],
"Germany": [(leftX, botY-mnY*5), "Germany", "property", 180, [14, 70, 200, 550, 750, 950], 90, 120, 0, "blue"],
"Italia": [(leftX, topY), "Italia", "property", 300, [22, 110, 330, 800, 975, 1150], 150, 200, 0, "blue"],
"France": [(leftX+mnX, topY), "France", "property", 200, [16, 80, 220, 600, 800, 1000], 100, 130, 0, "red"],
"Spain": [(leftX+mnX*2, topY), "Spain", "property", 200, [18, 90, 250, 700, 875, 1050], 100, 130, 0, "red"],
"UK": [(leftX+mnX*3, topY), "UK", "property", 240, [18, 90, 250, 700, 875, 1050], 120, 150, 0, "yellow"],
"Brazil": [(leftX+mnX*4, topY), "Brazil", "property", 240, [18, 90, 250, 700, 875, 1050], 120, 150, 0, "yellow"],
"Argentina": [(leftX+mnX*5, topY), "Argentina", "property", 240, [18, 90, 250, 700, 875, 1050], 120, 150, 0, "yellow"],
"Australia": [(rightX, topY), "Australia", "property", 400, [26, 130, 390, 900, 1100, 1275], 200, 300, 0, "yellow"],
"Mexico": [(rightX, topY+mnY), "Mexico", "property", 280, [20, 100, 300, 750, 925, 1100], 140, 180, 0, "green"],
"USA": [(rightX, topY+mnY*2), "USA", "property", 280, [22, 110, 330, 800, 975, 1150], 140, 180, 0, "green"],
"Canada": [(rightX, topY+mnY*3), "Canada", "property", 280, [22, 110, 330, 800, 975, 1150], 140, 180, 0, "green"],
"Japan": [(rightX, topY+mnY*4), "Japan", "property", 350, [24, 120, 360, 850, 1025, 1200], 175, 250, 0, "purple"],
"Korea": [(rightX, topY+mnY*5), "Korea", "property", 400, [26, 130, 390, 900, 1100, 1275], 200, 300, 0, "purple"],
"Go": [(rightX, botY), "Go", "other"],

        }


# The layout of the monopoly board

gameBoard = [

cards["Go"], cards["Taiwan"], cards["Philippines"],
cards["China"], cards["Singapore"],cards["Turkey"],
cards["Egypt"], cards["Greece"], cards["Denmark"],
cards["Sweden"],cards["Suisse"], cards["Germany"],
cards["Italia"], cards["France"], cards["Spain"],
cards["UK"], cards["Brazil"], cards["Argentina"],
cards["Australia"], cards["Mexico"], cards["USA"],
cards["Canada"], cards["Japan"], cards["Korea"]

            ]
