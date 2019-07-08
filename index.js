function hi(){
    document.write("1");
    var fs = require("fs");
    document.write("2");
var content = fs.readFileSync("data.json");
var jsonContent = JSON.parse(content);
var keys = Object.keys(jsonContent);
var min_year=2000;
var max_year = 2000;
for (var i = 0; i < keys.length; i++) {
    if(jsonContent[keys[i]]["year"]>1000 & jsonContent[keys[i]]["year"]<min_year){
        min_year = jsonContent[keys[i]]["year"];
    }
    if(jsonContent[keys[i]]["year"]>1000 & jsonContent[keys[i]]["year"]>max_year){
        max_year = jsonContent[keys[i]]["year"];
    }
  }
  document.write(min_year+"-"+max_year);
}