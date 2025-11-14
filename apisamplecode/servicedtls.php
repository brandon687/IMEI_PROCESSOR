<?php
	include 'header.htm';
	require_once('api/gsmfusion_api.php');
	$serviceType = $_REQUEST['st'] ? $_REQUEST['st'] : '0';
	$objGSMFUSIONAPI = new GSMFUSIONAPI();
	$objGSMFUSIONAPI->doAction('getservicedtls', array('st' => $serviceType));
	$objGSMFUSIONAPI->XmlToArray($objGSMFUSIONAPI->getResult());
	$arrayData = $objGSMFUSIONAPI->createArray();
	if(isset($arrayData['error']) && sizeof($arrayData['error']) > 0)
	{
		echo '<b>'.$arrayData['error'][0].'</b>';
		exit;
	}

	$RESPONSE_ARR = array();
	if(isset($arrayData['Services']['Service']) && sizeof($arrayData['Services']['Service']) > 0)
		$RESPONSE_ARR = $arrayData['Services']['Service'];
	$total = count($RESPONSE_ARR);
	echo '<table align="center" width="60%" class="tbl"><tr class="header"><th width="50%">Value to Send</th><th width="50%">Value To Show</th></tr>';
	for($count = 0; $count < $total; $count++)
	{
		$cssClass = $cssClass == '' ? 'class="alt"' : '';
		echo '<tr '.$cssClass.'><td>' . $RESPONSE_ARR[$count]['ServiceId'] . '</td><td>' . $RESPONSE_ARR[$count]['ServiceTitle'] . '</td></tr>';		
	}
	echo '</table>';
	include 'footer.htm';
?>