<?php
	include 'header.htm';
	require_once('api/gsmfusion_api.php');

	$objGSMFUSIONAPI = new GSMFUSIONAPI();
	$para = array();
	$para['networkId'] = '2';
	$para['fileName'] = '351685051003195.bcl';
	$fileContents = file_get_contents('351685051003195.bcl');
	$para['fileData'] = base64_encode($fileContents);

	$objGSMFUSIONAPI->doAction('placefileorder', $para);
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
		if(isset($arrayData['result']['fileorder']) && sizeof($arrayData['result']['fileorder']) > 0)
			$RESPONSE_ARR = $arrayData['result']['fileorder'];
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