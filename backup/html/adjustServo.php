<head>
<script type="text/javascript" src="/js/jquery.min.js"></script>
</head>
<body>
<?php

$jsonFile = '/var/www/ncwebsite/home/rubik/config.json';
$json = file_get_contents($jsonFile);
$jsonData = json_decode($json,true); 

$serial = $_GET['serial'];
$direction = $_GET['direction'];
$position = $_GET['position'];
$value = $jsonData[$direction][$position];
if ($position == 'in' OR $position == 'out'){
  $servo = $jsonData[$direction]["moveId"];
  } else {
  $servo = $jsonData[$direction]["turnId"];
}
$minValue = $value - 500;
$maxValue = $value + 500;

$cmd = "/var/www/scripts/moveServo.sh single $serial $servo $value";
$result = shell_exec($cmd);

echo "<table>";
echo "<tr><td>Location: $direction</td></tr>";
echo "<tr><td>Postion: $position</td></tr>";
echo "<tr><td>Servo: $servo</td></tr>";
echo "<tr><td>Value: $value</td></tr>";
echo "<tr><td></td></tr>";
echo "<form action='' method='POST'>";
echo "<div class='setValue'>";
echo "<tr><td><input type='number' id='slider' name='setValue' min='".$minValue."' max='".$maxValue."' value='".$value."' step=20 oninput='valueChange(this.value)'></td></tr>";
echo "<tr><td><p id='rangeValue'></p></td></tr>";
echo "</div>";
echo "<tr><td>";
echo "</td></tr>";
echo "<tr><td><input type=submit value=Submit></td></tr>";
echo "</form>";
echo "</table>";

if(isset($_POST["setValue"])){
  $jsonData[$direction][$position] = $_POST["setValue"];
  $newJsonString = json_encode($jsonData);
  file_put_contents($jsonFile, $newJsonString);
  echo "<script>window.opener.location.reload();";
  echo "window.close();</script>";
}

?>

<script>

function valueChange(val) {
  var slider = document.getElementById("slider");
  var output = document.getElementById("rangeValue");
  var serial = "<?php echo $_GET['serial']; ?>";
  var direction = "<?php echo $_GET['direction']; ?>";
  var servo = "<?php echo $servo; ?>";

  output.innerHTML = val; // Display the default value

  // Update the current value (each time you change the value)
  $.ajax({
    url:"testServo.php",
    method:'GET',
    data: {"serial": serial, "servo": servo, "value": val},
    error: error => {
      console.error(error)
    },
    success:function(response){
      console.log("Value: " + val);
    }
  })
}

</script>

</body>
