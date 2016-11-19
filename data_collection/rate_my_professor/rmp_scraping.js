var rmp = require("rmp-api");
var list_of_profs = ['Wenke Lee', 'Kishore Ramachandran', 'Rich Vuduc', 'Guy Lebanon', 'Nick Feamster', 'Wenke Lee', 'Milos Prvulovic', 'Alessandro Orso', 'Spencer Rugaber', 'Mayur Naik', 'Leo Mark', 'Mark Braunstein', 'David Joyner', 'Irfan Essa', 'Aaron Bobick', 'Charlie Brubaker', 'Thad Starner', 'Ashok Goel', 'Charles Isbell', 'Tucker Balch', 'Jimeng Sun', 'Sebastian Thrun', 'Ada Gavrilovska', 'Charles Isbell', 'Santosh Pande', 'Raheem Beyah'];
var curr_prof_data = new Array();
var all_prof_data = [];
var callback = function(professor) {
curr_prof_data= {
		"Name":null,
		"University":null,
		"Quality":null,
		"Easiness":null,
		"Helpfulness":null,
		"Average":null,
		"Chili":null,
		"URL":null,
		"Comment":null
                    };
	
if (professor === null) {
all_prof_data.push(curr_prof_data);
return;
}
//console.log("Name: " + professor.fname + " " + professor.lname);
//console.log("University: "+ professor.university);
//console.log("Quality: " + professor.quality);
//console.log("Easiness: " + professor.easiness);
//console.log("Helpfulness: " + professor.help);
//console.log("Average Grade: " + professor.grade);
//console.log("Chili: " + professor.chili);
//console.log("URL: " + professor.url);
//console.log("First comment: " + professor.comments[0]);
curr_prof_data= {
		"Name":professor.fname + " " + professor.lname,
		"University":professor.university,
		"Quality":professor.quality,
		"Easiness":professor.easiness,
		"Helpfulness":professor.help,
		"Average":professor.grade,
		"Chili":professor.chili,
		"URL":professor.url,
		"Comment":professor.comments[0]
                    };
all_prof_data.push(curr_prof_data);

//all_prof_data.push (professor.fname + " " + professor.lname, 
//                      professor.university, professor.quality, 
//                      professor.easiness, professor.help,
//                      professor.chili, professor.url,
//                      professor.comments[0]);
console.log(all_prof_data);
};

var gatech = rmp("Georgia Institute of Technology");
for (var i=0; i<list_of_profs.length; i++){
    console.log(list_of_profs[i]);
    gatech.get(list_of_profs[i], callback);
   // all_prof_data.push(curr_prof_data);
    //console.log(all_prof_data);
}
