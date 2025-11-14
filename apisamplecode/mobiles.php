<?php
	include 'header.htm';
	require_once('api/gsmfusion_api.php');
	
	$objGSMFUSIONAPI = new GSMFUSIONAPI();
	$objGSMFUSIONAPI->doAction('getmobiles', array());
	$objGSMFUSIONAPI->XmlToArray($objGSMFUSIONAPI->getResult());
	$arrayData = $objGSMFUSIONAPI->createArray();
	if(isset($arrayData['error']) && sizeof($arrayData['error']) > 0)
	{
		echo '<b>'.$arrayData['error'][0].'</b>';
		exit;
	}

	$RESPONSE_ARR = array();
	if(isset($arrayData['Mobiles']['Brand']) && sizeof($arrayData['Mobiles']['Brand']) > 0)
		$RESPONSE_ARR = $arrayData['Mobiles'];
	$total = count($RESPONSE_ARR);
	$Data = $RESPONSE_ARR;
	echo '<h2>MOBILES</h2><table align="center" width="100%">';
	foreach ($Data['Brand'] as $Brand)
	{
		echo '<tr class="alt"><td nowrap valign="top"><b>' . htmlspecialchars($Brand['Name']) . ' ('.$Brand['ID'].')</b></td>';
		foreach ($Brand['Mobile'] as $Mobile)
		{
			echo '<td valign="top" nowrap>' . htmlspecialchars($Mobile['Name']) . ' <br>ID: '.$Mobile['ID'].'</td>';
		}
		echo '</tr>';
	}
	echo('</table>');
	include 'footer.htm';
?>