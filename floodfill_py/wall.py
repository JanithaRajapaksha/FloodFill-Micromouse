class Wall:
    def __init__(self, x, y, wall_code):
        self.x = x
        self.y = y
        self.wall_code = wall_code

        '''Wall code:
        0: No wall
        N: North wall
        S: South wall
        W: West wall
        E: East wall
        
        NS: North and South walls
        WE: West and East walls
        WN: West and North walls
        SW: South and West walls
        NE: North and East walls
        ES: East and South walls
        
        WNE: West, North, and East walls
        NES: North, East, and South walls
        ESW: East, South, and West walls
        SWN: South, West, and North walls
        '''