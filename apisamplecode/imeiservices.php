<?php
	include 'header.htm';
	require_once('api/gsmfusion_api.php');
	
	$objGSMFUSIONAPI = new GSMFUSIONAPI();
	$objGSMFUSIONAPI->doAction('imeiservices', array());
	$objGSMFUSIONAPI->XmlToArray($objGSMFUSIONAPI->getResult());
	$arrayData = $objGSMFUSIONAPI->createArray();
	if(isset($arrayData['error']) && sizeof($arrayData['error']) > 0)
	{
		echo '<b>'.$arrayData['error'][0].'</b>';
		exit;
	}

	$RESPONSE_ARR = array();
	if(isset($arrayData['Packages']['Package']) && sizeof($arrayData['Packages']['Package']) > 0)
		$RESPONSE_ARR = $arrayData['Packages']['Package'];
	$total = count($RESPONSE_ARR);
	echo '<table align="center" width="60%" class="tbl"><tr class="header"><th>Service ID</th><th>Category</th><th>Service</th><th>Price</th>
	<th>Delivery Time</th><th>Service Detail</th></tr>';
	for($count = 0; $count < $total; $count++)
	{
		$cssClass = $cssClass == '' ? 'class="alt"' : '';
		echo '<tr '.$cssClass.'><td>' . $RESPONSE_ARR[$count]['PackageId'] . '</td><td>' . $RESPONSE_ARR[$count]['Category'] . '</td>
		<td>' . $RESPONSE_ARR[$count]['PackageTitle'] . '</td><td>' . $RESPONSE_ARR[$count]['PackagePrice'] . '</td>
		<td>' . $RESPONSE_ARR[$count]['TimeTaken'] . '</td><td>' . $RESPONSE_ARR[$count]['MustRead'] . '</td></tr>';		
	}
	echo '</table>';
	include 'footer.htm';
?>