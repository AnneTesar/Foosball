<?php 

$vids = scandir('c:\uwamp\www\output'); 

$videos = [];
foreach($vids as $vid) { 
	
	array_push($videos, $vid);
}

$videos = json_encode($videos);
echo $videos;

?>