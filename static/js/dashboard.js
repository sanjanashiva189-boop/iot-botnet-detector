let trafficChart;

const ctx = document.getElementById('trafficChart').getContext('2d');

trafficChart = new Chart(ctx, {

type:'line',

data:{
labels:[],
datasets:[{
label:'Network Traffic',
data:[]
}]
}

});


function updateData(){

fetch('/live_data')
.then(res => res.json())
.then(data => {

    // ✅ Network Traffic value
    document.getElementById("trafficValue").innerText = data.traffic + " GB";

    // ✅ Change %
    let changeText = data.change + "% vs yesterday";
    document.getElementById("trafficChange").innerText = changeText;

    // optional color
    if(data.change >= 0){
        document.getElementById("trafficChange").style.color = "green";
    } else {
        document.getElementById("trafficChange").style.color = "red";
    }

});
}

setInterval(updateData,3000);



// Detection Method Chart

new Chart(document.getElementById("methodChart"),{

type:'bar',

data:{
labels:[
'DPI',
'Behavior',
'Signature',
'ML',
'Flow',
'Honeypot'
],

datasets:[{
data:[94,88,82,91,76,69]
}]
}

});



// Geographic Chart

new Chart(document.getElementById("geoChart"),{

type:'pie',

data:{
labels:[
'China',
'Russia',
'USA',
'Brazil',
'India'
],

datasets:[{
data:[342,256,189,134,98]
}]
}

});



function loadPage(page){

window.location.href="/"+page;

}
