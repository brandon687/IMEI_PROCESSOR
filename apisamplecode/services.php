<?php
	require_once('api/gsmfusion_api.php');
	$objGSMFUSIONAPI = new GSMFUSIONAPI();
	$objGSMFUSIONAPI->doAction('getservices', array());
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
	for($count = 0; $count < $total; $count++)
	{
		echo '<a target="_blank" href="servicedtls.php?st='.str_replace("tbl_gf_", "", $RESPONSE_ARR[$count]['ServiceTbl']).'" class="link">'.$RESPONSE_ARR[$count]['ServiceName'].'</a> <br /><br />';
	}
?>