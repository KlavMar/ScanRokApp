class CoordScanOcrPlayers:
    def get_governor_id (self):
         roi =  (715, 180, 190, 40)
         return roi

    def get_governor_name(self):
        roi = 'input tap 620 250'
        return roi

    def get_power(self):
        roi = (874, 320, 180, 50)
        return roi 
    def get_kill_points(self):
        roi=  (1170, 320, 224, 40)
        return roi 
    
    def get_civilisation(self):
        roi = (1245,210,200,40)
        return roi 
    
    def get_alliance(self):
        roi = (580, 320, 270, 40)
        return roi 

    def get_tiers_kill(self):
        dict_of_tiers= dict()
        y0 =410
        for index in range(5):
            y = y0 + (index*45)
            roi=(1320,y,160,45)
            name=f"t{index+1}_kills"
 
            dict_of_tiers.update({name:roi})
        return dict_of_tiers

    def get_highest_power(self):
        highest_power = (1160, 270, 160, 50)
        return highest_power

    def get_victory(self):
        victory = (1160, 330, 160, 50) 
        return victory
    
    def get_defeat(self):
        defeat = (1200, 390, 120, 50)
        return defeat
    
    def get_deads(self):
        deads = (1160, 450, 160, 40)
        return deads
    
    def get_rss_gathered(self):
        rss_gathered = (1135, 630, 180, 40)
        return rss_gathered
    
    def get_rss_assistance(self):
        rss_assistance = (1135, 690, 180, 40)
        return rss_assistance
    
    def get_alliance_help(self):
        alliance_help = (1190, 750, 130, 40)
        return alliance_help
    

    def get_gov_info(self):
        """
        Governor ID et governor Name récupéré de façon annexe
        """
        return {
                "civilisation":self.get_civilisation(),
                "alliance":self.get_alliance(),
                "power":self.get_power(),
                "kill_points":self.get_kill_points()
                }

    def get_more_info(self):
        return {
        "highest_power" : self.get_highest_power(),
        "victory" :self.get_victory(),
        "defeat" : self.get_defeat(),
        "deads" : self.get_deads(),
        "ressources_gathered" : self.get_rss_gathered(),
        "ressources_assistance" : self.get_rss_assistance(),
        "alliance_help" : self.get_alliance_help()
        }

    def get_schema(self):

        return {
            "governor_id":int,
            "id_kingdom":int,
            "civilisation":str,
            "alliance":str,
            "power":int,
            "kill_points":int,
            "t1_kills":int,
            "t2_kills":int,
            "t3_kills":int,
            "t4_kills":int,
            "t5_kills":int,
            "highest_power" : int,
            "victory" :int,
            "defeat" : int,
            "deads" :int,
            "ressources_gathered" : int,
            "ressources_assistance" : int,
            "alliance_help" :int
        }
    
    def get_order_column(self):
        columns=[
            "id_kingdom",
            "name_alliance",
            "tags" ,
            "governor_id",
            "governor_name",
            "power" ,
            "kill_points" ,
            "t1_kills" ,
            "t2_kills" ,
            "t3_kills" ,
            "t4_kills" ,
            "t5_kills" ,
            "highest_power" ,
            "victory" ,
            "defeat" ,
            "deads" ,
            "ressources_gathered" ,
            "ressources_assistance" ,
            "alliance_help",
            "date",
            "civilisation"
            
        ]
        return columns
    

class CoordsGamesInteraction:
    open_gov = 'input tap 70 54'
    open_ranking_menu = "input tap 387 720"
    open_ranking_power = "input tap 280 500"

    input_gov_close = 'input tap 1454 90'
    input_open_kill_tiers ='input tap 1167 314'
    input_open_more_info = 'input tap 230 730'
    input_close_more_info = 'input tap 1400 55'

