
def main():
    
    #initialization and setup
    settings = {
        "light": ["1","2","3","4","5"],
        "left_star": ["0", "1","2","3","4","5"],
        "right_star"  : ["0", "1","2","3","4","5"]
    }

    at = AnimTools(settings).init_with_first()

    #define sequences
    at.sequence("Tent pulse").pulse('light', 1000)
    at.sequence("Left shooting star").full_transition("left_star", 1000).set("left_star", "0")
    at.sequence("Right shooting star").full_transition("right_star", 1000).set("right_star", "0")

    #Run
    at.sequence("Tent pulse").loop_background()

    #wait(15000)

    at.sequence("Left shooting star").once()

    #wait(15000)

    at.sequence("Right shooting star").once()

    wait(4000)