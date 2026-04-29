<head>
<style>
#full-table {
  background-image: url('Otvinta-rubik.png');
  background-repeat: no-repeat;
  background-position: 220px 250px;
  margin-top:50px;
  margin-left:300px;
}
#down-table {
  margin-top:110px;
}
#popup {
	location=0;
	width=600;
	height=400;
	left=300;
	top=300;
}
</style>
<script>
// When the user clicks on <div>, open the popup
function openForm() {
  document.getElementById("myForm").style.display = "block";
}

function closeForm() {
  document.getElementById("myForm").style.display = "none";
}

function delay() {
  var popup = document.getElementById("myPopup");
  popup.classList.toggle("show");
}
</script>
</head>
<body>

<?php

$serial = '/dev/ttyACM0';
#$jsonFile = '/var/www/scripts/config.json';
$jsonFile = '/var/www/ncwebsite/home/rubik/config.json';
$json = file_get_contents($jsonFile);
$jsonData = json_decode($json,true); 

$left = $jsonData["left"]; 
$right = $jsonData["right"]; 
$up = $jsonData["up"]; 
$down = $jsonData["down"]; 
$delay = $jsonData["delay"];

/*
  "Right":{
    "turnId":0,
    "0":1650,
    "90":4200,
    "180":6850,
    "270":9500,
    "moveId":2,
    "in":7000,
    "out":4000
  },
*/

$rTurnId = $right["turnId"];
$r0 = $right["0"];
$r90 = $right["90"];
$r180 = $right["180"];
$r270 = $right["270"];
$rMoveId = $right["moveId"];
$rIn = $right["in"];
$rOut = $right["out"];

$lTurnId = $left["turnId"];
$l0 = $left["0"];
$l90 = $left["90"];
$l180 = $left["180"];
$l270 = $left["270"];
$lMoveId = $left["moveId"];
$lIn = $left["in"];
$lOut = $left["out"];

$uTurnId = $up["turnId"];
$u0 = $up["0"];
$u90 = $up["90"];
$u180 = $up["180"];
$u270 = $up["270"];
$uMoveId = $up["moveId"];
$uIn = $up["in"];
$uOut = $up["out"];

$dTurnId = $down["turnId"];
$d0 = $down["0"];
$d90 = $down["90"];
$d180 = $down["180"];
$d270 = $down["270"];
$dMoveId = $down["moveId"];
$dIn = $down["in"];
$dOut = $down["out"];

/*
  "Delay":{
    "90":350,
    "180":700,
    "Move":350
  }
*/

$delay90 = $delay["90"];
$delay180 = $delay["180"];
$delayMove = $delay["move"];

echo "<table id='full-table'>";
echo "<tr>";
echo "<th style='width:300px'></th>";
echo "<th style='width:300px'>";
echo "<th style='width:300px'>";
echo "</tr>";

echo "<tr style='height:300px'><td></td><td>";

echo "<table id='up-table'>";
echo "<tr><td width='50px'>Position</td><td>Value</td><td>Adjust</td></tr>";
echo "<tr><td>0</td><td><input type=int disabled id='u0' value=$u0 size='4'></td><td><button class='button' onClick=\"window.open('adjustServo.php?direction=up&position=0&value=$u0&serial=$serial','popup','location=0,width=600,height=300,left=300,top=300'); return false; id='popup'\">Calibrate</button></td></tr>";
echo "<tr><td>90</td><td><input type=int disabled id='u90' value=$u90 size='4'></td><td><button class='button' onClick=\"window.open('adjustServo.php?direction=up&position=90&value=$u90&serial=$serial','popup','location=0,width=600,height=300,left=300,top=300'); return false; id='popup'\">Calibrate</button></td></tr>";
echo "<tr><td>180</td><td><input type=int disabled id='u180' value=$u180 size='4'></td><td><button class='button' onClick=\"window.open('adjustServo.php?direction=up&position=180&value=$u180&serial=$serial','popup','location=0,width=600,height=300,left=300,top=300'); return false; id='popup'\">Calibrate</button></td></tr>";
echo "<tr><td>270</td><td><input type=int disabled id='u270' value=$u270 size='4'></td><td><button class='button' onClick=\"window.open('adjustServo.php?direction=up&position=270&value=$u270&serial=$serial','popup','location=0,width=600,height=300,left=300,top=300'); return false; id='popup'\">Calibrate</button></td></tr>";
echo "<tr><td colspan=3> </td></tr>";
echo "<tr><td colspan=3>Move</td></tr>";
echo "<tr><td>In</td><td><input type=int disabled id='uIn' value=$uIn size='4'></td><td><button class='button' onClick=\"window.open('adjustServo.php?direction=up&position=in&value=$uIn&serial=$serial','popup','location=0,width=600,height=300,left=300,top=300'); return false; id='popup'\">Calibrate</button></td></tr>";
echo "<tr><td>Out</td><td><input type=int disabled id='uOut' value=$uOut size='4'></td><td><button class='button' onClick=\"window.open('adjustServo.php?direction=up&position=out&value=$uOut&serial=$serial','popup','location=0,width=600,height=300,left=300,top=300'); return false; id='popup'\">Calibrate</button></td></tr>";
echo "</table>";

echo "</td><td></td></tr>";
echo "<tr style='height:300px'><td>";

echo "<table id='right-table'>";
echo "<tr><td width='50px'>Position</td><td>Value</td><td>Adjust</td></tr>";
echo "<tr><td>0</td><td><input type=int disabled id='r0' value=$r0 size='4'></td><td><button class='button' onClick=\"window.open('adjustServo.php?direction=right&position=0&value=$r0&serial=$serial','popup','location=0,width=600,height=300,left=300,top=300'); return false; id='popup'\">Calibrate</button></td></tr>";
echo "<tr><td>90</td><td><input type=int disabled id='r90' value=$r90 size='4'></td><td><button class='button' onClick=\"window.open('adjustServo.php?direction=right&position=90&value=$r90&serial=$serial','popup','location=0,width=600,height=300,left=300,top=300'); return false; id='popup'\">Calibrate</button></td></tr>";
echo "<tr><td>180</td><td><input type=int disabled id='r180' value=$r180 size='4'></td><td><button class='button' onClick=\"window.open('adjustServo.php?direction=right&position=180&value=$r180&serial=$serial','popup','location=0,width=600,height=300,left=300,top=300'); return false; id='popup'\">Calibrate</button></td></tr>";
echo "<tr><td>270</td><td><input type=int disabled id='r270' value=$r270 size='4'></td><td><button class='button' onClick=\"window.open('adjustServo.php?direction=right&position=270&value=$r270&serial=$serial','popup','location=0,width=600,height=300,left=300,top=300'); return false; id='popup'\">Calibrate</button></td></tr>";
echo "<tr><td colspan=3> </td></tr>";
echo "<tr><td colspan=3>Move</td></tr>";
echo "<tr><td>In</td><td><input type=int disabled id='rIn' value=$rIn size='4'></td><td><button class='button' onClick=\"window.open('adjustServo.php?direction=right&position=in&value=$rIn&serial=$serial','popup','location=0,width=600,height=300,left=300,top=300'); return false; id='popup'\">Calibrate</button></td></tr>";
echo "<tr><td>Out</td><td><input type=int disabled id='rOut' value=$rOut size='4'></td><td><button class='button' onClick=\"window.open('adjustServo.php?direction=right&position=out&value=$rOut&serial=$serial','popup','location=0,width=600,height=300,left=300,top=300'); return false; id='popup'\">Calibrate</button></td></tr>";
echo "</table>";

echo "</td><td></td><td>";

echo "<table id='left-table'>";
echo "<tr><td width='50px'>Position</td><td>Value</td><td>Adjust</td></tr>";
echo "<tr><td>0</td><td><input type=int disabled id='l0' value=$l0 size='4'></td><td><button class='button' onClick=\"window.open('adjustServo.php?direction=left&position=0&value=$l0&serial=$serial','popup','location=0,width=600,height=300,left=300,top=300'); return false; id='popup'\">Calibrate</button></td></tr>";
echo "<tr><td>90</td><td><input type=int disabled id='l90' value=$l90 size='4'></td><td><button class='button' onClick=\"window.open('adjustServo.php?direction=left&position=90&value=$l90&serial=$serial','popup','location=0,width=600,height=300,left=300,top=300'); return false; id='popup'\">Calibrate</button></td></tr>";
echo "<tr><td>180</td><td><input type=int disabled id='l180' value=$l180 size='4'></td><td><button class='button' onClick=\"window.open('adjustServo.php?direction=left&position=180&value=$l180&serial=$serial','popup','location=0,width=600,height=300,left=300,top=300'); return false; id='popup'\">Calibrate</button></td></tr>";
echo "<tr><td>270</td><td><input type=int disabled id='l270' value=$l270 size='4'></td><td><button class='button' onClick=\"window.open('adjustServo.php?direction=left&position=270&value=$l270&serial=$serial','popup','location=0,width=600,height=300,left=300,top=300'); return false; id='popup'\">Calibrate</button></td></tr>";
echo "<tr><td colspan=3> </td></tr>";
echo "<tr><td colspan=3>Move</td></tr>";
echo "<tr><td>In</td><td><input type=int disabled id='lIn' value=$lIn size='4'></td><td><button class='button' onClick=\"window.open('adjustServo.php?direction=left&position=in&value=$lIn&serial=$serial','popup','location=0,width=600,height=300,left=300,top=300'); return false; id='popup'\">Calibrate</button></td></tr>";
echo "<tr><td>Out</td><td><input type=int disabled id='lOut' value=$lOut size='4'></td><td><button class='button' onClick=\"window.open('adjustServo.php?direction=left&position=out&value=$lOut&serial=$serial','popup','location=0,width=600,height=300,left=300,top=300'); return false; id='popup'\">Calibrate</button></td></tr>";
echo "</table>";

echo "</td></tr><tr style='height:300px'><td>";
echo "<table id='delay-table'><form action='' method='POST'>";
echo "<tr><td width='50px'>Delay</td></tr>";
echo "<tr><td>90°</td><td>";
echo "<input type=int name='delay90' value=$delay90 size='4'><br></td><td>";
echo "<tr><td>180°</td><td>";
echo "<input type=int name='delay180' value=$delay180 size='4'><br></td><td>";
echo "<tr><td>Move</td><td>";
echo "<input type=int name='delayMove' value=$delayMove size='4'><br></td></tr>";
echo "<tr><td><input type=submit value=Submit></td></tr>";
echo "</form></table>";
echo "</td><td>";

echo "<table id='down-table'>";
echo "<tr><td width='50px'>Position</td><td>Value</td><td>Adjust</td></tr>";
echo "<tr><td>0</td><td><input type=int disabled id='d0' value=$d0 size='4'></td><td><button class='button' onClick=\"window.open('adjustServo.php?direction=down&position=0&value=$d0&serial=$serial','popup','location=0,width=600,height=300,left=300,top=300'); return false; id='popup'\">Calibrate</button></td></tr>";
echo "<tr><td>90</td><td><input type=int disabled id='d90' value=$d90 size='4'></td><td><button class='button' onClick=\"window.open('adjustServo.php?direction=down&position=90&value=$d90&serial=$serial','popup','location=0,width=600,height=300,left=300,top=300'); return false; id='popup'\">Calibrate</button></td></tr>";
echo "<tr><td>180</td><td><input type=int disabled id='d180' value=$d180 size='4'></td><td><button class='button' onClick=\"window.open('adjustServo.php?direction=down&position=180&value=$d180&serial=$serial','popup','location=0,width=600,height=300,left=300,top=300'); return false; id='popup'\">Calibrate</button></td></tr>";
echo "<tr><td>270</td><td><input type=int disabled id='d270' value=$d270 size='4'></td><td><button class='button' onClick=\"window.open('adjustServo.php?direction=down&position=270&value=$d270&serial=$serial','popup','location=0,width=600,height=300,left=300,top=300'); return false; id='popup'\">Calibrate</button></td></tr>";
echo "<tr><td colspan=3> </td></tr>";
echo "<tr><td colspan=3>Move</td></tr>";
echo "<tr><td>In</td><td><input type=int disabled id='dIn' value=$dIn size='4'></td><td><button class='button' onClick=\"window.open('adjustServo.php?direction=down&position=in&value=$dIn&serial=$serial','popup','location=0,width=600,height=300,left=300,top=300'); return false; id='popup'\">Calibrate</button></td></tr>";
echo "<tr><td>Out</td><td><input type=int disabled id='dOut' value=$dOut size='4'></td><td><button class='button' onClick=\"window.open('adjustServo.php?direction=down&position=out&value=$dOut&serial=$serial','popup','location=0,width=600,height=300,left=300,top=300'); return false; id='popup'\">Calibrate</button></td></tr>";
echo "</table>";

echo "</td><td></td></tr>";

if(isset($_POST["delay90"]) OR isset($_POST["delay180"]) OR isset($_POST["delayMove"])){
  $jsonData["delay"]["90"] = $_POST["delay90"];
  $jsonData["delay"]["180"] = $_POST["delay180"];
  $jsonData["delay"]["270"] = $_POST["delay270"];
  $newJsonString = json_encode($jsonData);
  file_put_contents($jsonFile, $newJsonString);
  echo "<script>window.reload();</script>";
}

?>
</table>
</body>
