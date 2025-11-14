<?php
	include 'header.htm';
	require_once('api/gsmfusion_api.php');

	$objGSMFUSIONAPI = new GSMFUSIONAPI();

	$objGSMFUSIONAPI->doAction('placeorder', array('imei' => '111199122222005', 'networkId' => '1'));

	/*
	POSSIBLE PARAMTERS
	'imei' => '621488122222119,621488122222333,621488122222220';
	'serviceId' => '1234';
	'networkId' => '12';
	'modelId' => '123';
	'providerId' => '1234';
	'operatorId' => '1234';
	'mobileId' => '1234';
	'mep' => 'MEP-04598-005';
	'serialNo' => '111';
	'network' => '111';
	'type' => '1,2,3';
	'locks' => '1';
	'prd' => '1234';
	'pin' => '1234';
	'kbh' => '1234';
	'modelNo' => '1234';
	'zte' => '1234';
	'otherId' => '1234';
	'other' => '1234';
	*/
	$objGSMFUSIONAPI->XmlToArray($objGSMFUSIONAPI->getResult());
	$arrayData = $objGSMFUSIONAPI->createArray();
	if(isset($arrayData['error']) && sizeof($arrayData['error']) > 0)
	{
		echo '<b>'.$arrayData['error'][0].'</b>';
		exit;
	}

	$RESPONSE_ARR = array();
	$RESPONSE_ARR_DUP = array();
	//$RESPONSE_ARR_IMEI_ERR = array();
	if(isset($arrayData['result']['imeis']) && sizeof($arrayData['result']['imeis']) > 0)
		$RESPONSE_ARR = $arrayData['result']['imeis'];

	if(isset($arrayData['result']['imeiduplicates']) && sizeof($arrayData['result']['imeiduplicates']) > 0)
		$RESPONSE_ARR_DUP = $arrayData['result']['imeiduplicates'];
/*
	if(isset($arrayData['result']['imeierrors']) && sizeof($arrayData['result']['imeierrors']) > 0)
		$RESPONSE_ARR_IMEI_ERR = $arrayData['result']['imeierrors'];
*/
	$total = count($RESPONSE_ARR);
	if($total > 0)
	{
		echo '<table align="left" width="60%" class="tbl">';
		echo '<tr><td colspan="3">Following IMIE(s) have been sent.</td></tr>';
		echo '<tr class="header">';
			echo '<th width="20%">ID</th>';
			echo '<th width="40%">IMEI</th>';
			echo '<th width="40%">Status</th>';
		echo '</tr>';
		for($count = 0; $count < $total; $count++)
		{
			$cssClass = $cssClass == '' ? 'class="alt"' : '';
			echo '<tr '.$cssClass.'><td>' . $RESPONSE_ARR[$count]['id'] . '</td><td>' . $RESPONSE_ARR[$count]['imei'] . '</td><td>' . $RESPONSE_ARR[$count]['status'] . '</td></tr>';		
		}
		echo '</table>';
	}
	$total_errors = count($RESPONSE_ARR_DUP);
	if($total_errors > 0)
	{
		echo '<table align="left" width="60%" class="tbl">';
		echo '<tr><td>Following IMIE(s) are already in the system, so they can not be repeated.</td></tr>';
		echo '<tr class="header"><th width="100%">IMEI</th></tr>';
		$arrDupIMEIS = explode(',', $RESPONSE_ARR_DUP[0]['imei']);
		$totalDupIMES = count($arrDupIMEIS);
		for($count = 0; $count < $totalDupIMES; $count++)
		{
			$cssClass = $cssClass == '' ? 'class="alt"' : '';
			echo '<tr '.$cssClass.'><td>' . $arrDupIMEIS[$count] . '</td></tr>';
		}
		echo '</table>';
	}
/*
	$total_dup = count($RESPONSE_ARR_IMEI_ERR);
	if($total_dup > 0)
	{
		echo '<table align="left" width="60%" class="tbl">';
		echo '<tr><td>Following IMIE(s) could not be sent, due to the following mentioned issues.</td></tr>';
		echo '<tr class="header"><th width="30%">IMEI</th><th width="70%">IMEI</th></tr>';
		for($count = 0; $count < $total_dup; $count++)
		{
			$cssClass = $cssClass == '' ? 'class="alt"' : '';
			echo '<tr '.$cssClass.'><td>' . $RESPONSE_ARR_IMEI_ERR[$count]['imei'] . '</td><td>' . $RESPONSE_ARR_IMEI_ERR[$count]['error'] . '</td></tr>';
		}
		echo '</table>';
	}*/
	include 'footer.htm';
?>