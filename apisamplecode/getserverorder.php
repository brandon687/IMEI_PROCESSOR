<?php
	include 'header.htm';
	require_once('api/gsmfusion_api.php');
	
	$objGSMFUSIONAPI = new GSMFUSIONAPI();
	$objGSMFUSIONAPI->doAction('getserverorder', array('orderId' => '3'));
	$objGSMFUSIONAPI->XmlToArray($objGSMFUSIONAPI->getResult());
	$arrayData = $objGSMFUSIONAPI->createArray();
	$RESPONSE_ARR = array();
	
	if(isset($arrayData['error']) && sizeof($arrayData['error']) > 0)
	{
		echo '<b>'.$arrayData['error'][0].'</b>';
		exit;
	}

	if(isset($arrayData['result']['serverorder']) && sizeof($arrayData['result']['serverorder']) > 0)
		$RESPONSE_ARR = $arrayData['result']['serverorder'];
	$total = count($RESPONSE_ARR);

	echo '<table align="center" width="95%" class="tbl">';
	echo '<tr>';
		echo '<th>Package</th>';
		echo '<th>Status ID</th>';
		echo '<th>Status</th>';
		echo '<th>Code</th>';
		echo '<th>Requested At</th>';
	echo '</tr>';
	for($count = 0; $count < $total; $count++)
	{
		$cssClass = $cssClass == '' ? 'class="alt"' : '';
		echo '	<tr '.$cssClass.'><td>'.$RESPONSE_ARR[$count]['package'].'</td><td>'.$RESPONSE_ARR[$count]['statusId'].'</td>
		<td>'.$RESPONSE_ARR[$count]['status'].'</td><td>'.$RESPONSE_ARR[$count]['code'].'</td><td>'.$RESPONSE_ARR[$count]['requestedat'].'</td></tr>';
	}
	echo '</table>';
	include 'footer.htm';
?>