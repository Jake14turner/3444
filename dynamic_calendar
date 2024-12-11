const calendar = document.querySelector(".calendar"),
date = document.querySelector(".date"),
daysContainer = document.querySelector(".days"),
prev = document.querySelector(".prev"),
next = document.querySelector(".next");
todayBtn = document.querySelector(".today-btn"),
gotoBtn = document.querySelector(".goto-btn"),
dateInput = document.querySelector(".date-input");

let today = new Date();
let activeDay;
let month = today.getMonth();
let year = today.getFullYear();
const months =[
    "January", 
    "February", 
    "March", 
    "April", 
    "May", 
    "June", 
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]
// function to add days
function initCalendar(){
    //first day of the month
    const firstDay = new Date(year, month, 1);
    //last day of the month, 0 mean the last day of the previous month-current month
    const lastDay = new Date(year, month+1, 0);
    //last day of previous month because O automatically set it to last day of previous month
    const prevLastDay = new Date(year, month, 0);
    //Number of days in the previous month
    const prevDays = prevLastDay.getDate();
    //Number of days in the current month
    const LastDate = lastDay.getDate();
    // Day of the week the month starts on
    const day = firstDay.getDay();
    //  Remaining days for next month
    const nextDays = 7 - lastDay.getDay()-1;
//update date to top of calendar
date.innerHTML =months[month] +" "+ year; 
 //adding days on dom
 let days = "";
 //prev month days
 for (let x= day; x > 0;x--){
    //The class day is used to style all days, and prev-date can be used to style days from the previous month
    days +=`<div class= "day prev-date" >${prevDays - x + 1}</div>`;
 }
//current month days
for (let i=1; i<= LastDate; i++){
    //if day is today add class today
    if (i === new Date().getDate() && 
    year === new Date().getFullYear()&& 
    month == new Date().getMonth() ){
        days +=`<div class= "day today" >${i}</div>`;        
    }
    // add remaining as it is
    else{
        days += `<div class ="day">${i}</div>`;
    }
    }
//next  month days
for(let j =1; j <= nextDays; j++){
    days +=`<div class="day next-date" >${j}</div>`;
}
daysContainer.innerHTML = days;
}
initCalendar();
//prev month 
function prevMonth(){
    month--;
    if(month <0){
        month = 11;
        year--;
    }
    initCalendar();

}
// next month
function nextMonth(){
    month++;
    if (month > 11){
        month = 0;
        year++;
    }
    initCalendar();
}
//add eventListnner on prev and next
prev.addEventListener("click",prevMonth);
next.addEventListener("click", nextMonth);
// lets add togo date and goto today functionality
todayBtn.addEventListener("click", ()=>{
    today = new Date();
    month = today.getMonth();
    year = today.getFullYear();
    initCalendar();
});
 dateInput.addEventListener("input",(e)=>{
    dateInput.value = dateInput.value.replace(/[^0-9/]/g,"");
    if (dateInput.value.length ===2){
        dateInput.value +="/";

    }
    if (dateInput.value.lenth >7){
        // don't allow more than 7 character
        dateInput.value = dateInput.value.slice(0,7);
    }
    //if backspace pressed
    if(e.inputType ==="deleteContentBackward"){
        if(dateInput.value.length === 3){
            dateInput.value = dateInput.value.slice(0,2);
        }
    }

 });
  gotoBtn.addEventListener("click", gotoDate);
  //function to go to entered date
  function gotoDate(){
    const dateArr = dateInput.value.split("/");
    //some data validation
    if(dateArr.length ===2){
        if(dateArr[0]>0 && dateArr[0]<13 && dateArr[1].length ===4){
            month = dateArr[0]-1;
            year = dateArr[1];
            initCalendar();
            return;
        }
    }
    //if invalid date
    alert("invalid date");
  }
