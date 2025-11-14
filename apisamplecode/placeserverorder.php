<?php
	include 'header.htm';
	require_once('api/gsmfusion_api.php');

	$objGSMFUSIONAPI = new GSMFUSIONAPI();

	$objGSMFUSIONAPI->doAction('placeserverorder', array('serviceId' => '1'));

	/*
	POSSIBLE PARAMTERS
	'serialno_U4L6' => 'xxxxxxxxxxxxxx'; // For Serial No.
	'email_B5D9' => 'xxxxxxxxxxxxxx'; // For Email
	'serviceId' => '12'; // For Service ID
	'quantity_G7V7' => 'xxxxxxxxxxxxxx'; // For Quantity
	'username_K4I8' => 'xxxxxxxxxxxxxx'; // For Username
	*/
	$objGSMFUSIONAPI->XmlToArray($objGSMFUSIONAPI->getResult());
	$arrayData = $objGSMFUSIONAPI->createArray();
	if(isset($arrayData['error']) && sizeof($arrayData['error']) > 0)
	{
		echo '<b>'.$arrayData['error'][0].'</b>';
		exit;
	}
	else
	{
		$RESPONSE_ARR = array();
		if(isset($arrayData['result']['order']) && sizeof($arrayData['result']['order']) > 0)
			$RESPONSE_ARR = $arrayData['result']['order'];
		$total = count($RESPONSE_ARR);
		if($total > 0)
		{
			$id = $RESPONSE_ARR[0]['id'];
			$status = $RESPONSE_ARR[0]['status'];
			echo '<table align="left" width="60%" class="tbl">';
			echo '<tr><td colspan="3">Following Order has been sent.</td></tr>';
			echo '<tr class="header">';
				echo '<th>Order ID</th>';
				echo '<th>Order Status</th>';
			echo '</tr>';
			echo '<tr '.$cssClass.'><td>' . $id . '</td><td>' . $status . '</td></tr>';
			echo '</table>';
		}		
	}
	include 'footer.htm';
?>