<?php
	include 'header.htm';
	require_once('api/gsmfusion_api.php');
	
	$objGSMFUSIONAPI = new GSMFUSIONAPI();
	$objGSMFUSIONAPI->doAction('getproviders', array());
	$objGSMFUSIONAPI->XmlToArray($objGSMFUSIONAPI->getResult());
	$arrayData = $objGSMFUSIONAPI->createArray();
	if(isset($arrayData['error']) && sizeof($arrayData['error']) > 0)
	{
		echo '<b>'.$arrayData['error'][0].'</b>';
		exit;
	}

	$RESPONSE_ARR = array();
	if(isset($arrayData['Networks']['Country']) && sizeof($arrayData['Networks']['Country']) > 0)
		$RESPONSE_ARR = $arrayData['Networks'];
	$total = count($RESPONSE_ARR);
	$Data = $RESPONSE_ARR;
	echo '<h2>NEWORKS</h2><table align="center" width="100%">';
	foreach ($Data['Country'] as $Country)
	{
		echo '<tr class="alt">';
		echo '<td nowrap valign="top"><b>' . htmlspecialchars($Country['Name']) . ' ('.$Country['ID'].')</b></td>';
		foreach ($Country['Network'] as $Network)
		{
			echo '<td valign="top">' . htmlspecialchars($Network['Name']) . '<br>ID: '.$Network['ID'].'</td>';
		}
		echo '</tr>';
	}
	echo '</table>';

/*	echo '<table align="center" width="60%" class="tbl"><tr class="header"><th width="50%">ID</th><th width="50%">Country</th></tr>';
	for($count = 0; $count < $total; $count++)
	{
		$cssClass = $cssClass == '' ? 'class="alt"' : '';
		echo '<tr '.$cssClass.'><td>' . $RESPONSE_ARR[$count]['ID'] . '</td><td>' . $RESPONSE_ARR[$count]['Name'] . '</td></tr>';		
	}
	echo '</table>';*/
	include 'footer.htm';
?>