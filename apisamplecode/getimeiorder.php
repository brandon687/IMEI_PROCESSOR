<?php
	include 'header.htm';
	require_once('api/gsmfusion_api.php');
	
	$objGSMFUSIONAPI = new GSMFUSIONAPI();
	$objGSMFUSIONAPI->doAction('getimeis', array('orderIds' => '1'));
	$objGSMFUSIONAPI->XmlToArray($objGSMFUSIONAPI->getResult());
	$arrayData = $objGSMFUSIONAPI->createArray();

	$RESPONSE_ARR = array();
	
	if(isset($arrayData['error']) && sizeof($arrayData['error']) > 0)
	{
		echo '<b>'.$arrayData['error'][0].'</b>';
		exit;
	}

	if(isset($arrayData['result']['imeis']) && sizeof($arrayData['result']['imeis']) > 0)
		$RESPONSE_ARR = $arrayData['result']['imeis'];
	$total = count($RESPONSE_ARR);

	echo '<table align="center" width="95%" class="tbl">';
	echo '<tr>';
		echo '<th width="5%">ID</th>';
		echo '<th width="25%">Package</th>';
		echo '<th width="15%">IMEI</th>';
		echo '<th width="15%">Status</th>';
		echo '<th width="25%">Code</th>';
		echo '<th width="15%">Requested At</th>';
	echo '</tr>';
	for($count = 0; $count < $total; $count++)
	{
		$cssClass = $cssClass == '' ? 'class="alt"' : '';
		echo '	<tr '.$cssClass.'><td>'.$RESPONSE_ARR[$count]['id'].'</td><td>'.$RESPONSE_ARR[$count]['package'].'</td><td>'.$RESPONSE_ARR[$count]['imei'].'</td>
				<td>'.$RESPONSE_ARR[$count]['status'].'</td><td>'.$RESPONSE_ARR[$count]['code'].'</td><td>'.$RESPONSE_ARR[$count]['requestedat'].'</td></tr>';
	}
	echo '</table>';
	include 'footer.htm';
?>