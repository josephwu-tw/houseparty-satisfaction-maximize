class GUEST:
    def __init__(self, name, age, intimacy_level):
        self.name = name
        self.age = age
        self.gender = None
        self.relationship_type = None
        self.intimacy_level = intimacy_level
        
        # 食物偏好（喜欢分数默认 0）
        self.food_preferences = {
            "fried_chicken": 0,
            "chips": 0,
            "sandwich": 0,
            "cookies": 0,
            "sweeties": 0
        }
        
        # 饮料偏好（喜欢分数默认 0）
        self.beverage_preferences = {
            "soda": 0,
            "juice": 0,
            "black_tea": 0
        }   
    
    #转成字典   
    def to_dict(self):
        return {
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "relationship_type": self.relationship_type,
            "intimacy_level": self.intimacy_level,
            "food_preferences": self.food_preferences,
            "beverage_preferences": self.beverage_preferences
       }
    
    #导出jason
    def to_json(self, indent=2):
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

