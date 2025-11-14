<?php
class GSMFUSIONAPI
{
	var $objCurl;
	var $result = array();
	var $API_KEY = 'C0H6-T2S9-H9A0-G0T9-X3N7';
	var $USER_NAME = 'username';
	var $URL = 'http://sitetoconnect.com/';
	var $xml='';

	function getResult()
	{
		return $this->result;
	}
		
	function checkError($result)
	{
		if(isset($result['ERR']))
		{
			echo '<h2> Error Code: ' . $result['STATUS'] . '</h2>';
			echo '<h3>' . $result['ERR'] . '</h3>';
			exit;
		}
	}
	
    function doAction($toDo, $parameters = array())
    {
		if (is_string($toDo))
		{
			if (is_array($parameters))
			{
				$parameters['apiKey'] = $this->API_KEY;
				$parameters['userId'] = $this->USER_NAME;
				$parameters['action'] = $toDo;
				$this->objCurl = curl_init( );
				curl_setopt( $this->objCurl, CURLOPT_HEADER, false );
				curl_setopt( $this->objCurl, CURLOPT_USERAGENT, $_SERVER['HTTP_USER_AGENT']);
				curl_setopt( $this->objCurl, CURLOPT_FOLLOWLOCATION, true );
				curl_setopt( $this->objCurl, CURLOPT_RETURNTRANSFER, true );
				if( is_array( $parameters ) ):
					$vars = implode( '&', $parameters);
				endif;
				curl_setopt( $this->objCurl, CURLOPT_URL, $this->URL.'/gsmfusion_api/index.php');
				curl_setopt( $this->objCurl, CURLOPT_POST, true );
				curl_setopt( $this->objCurl, CURLOPT_POSTFIELDS, $parameters);
				$this->result = curl_exec( $this->objCurl );
				curl_close($this->objCurl);
			}
		}
    }

	function XmlToArray($xml)
	{
	   $this->xml = $xml;	
	}

	function _struct_to_array($values, &$i)
	{
		$child = array(); 
		if (isset($values[$i]['value'])) array_push($child, $values[$i]['value']); 
		
		while ($i++ < count($values)) { 
			switch ($values[$i]['type']) { 
				case 'cdata': 
            	array_push($child, $values[$i]['value']); 
				break; 
				
				case 'complete': 
					$name = $values[$i]['tag']; 
					if(!empty($name)){
					$child[$name]= ($values[$i]['value'])?($values[$i]['value']):''; 
					if(isset($values[$i]['attributes'])) {					
						$child[$name] = $values[$i]['attributes']; 
					} 
				}	
          	break; 
				
				case 'open': 
					$name = $values[$i]['tag']; 
					$size = isset($child[$name]) ? sizeof($child[$name]) : 0;
					$child[$name][$size] = $this->_struct_to_array($values, $i); 
				break;
				
				case 'close': 
            	return $child; 
				break; 
			}
		}
		return $child; 
	}//_struct_to_array
	function createArray()
	{ 
		$xml    = $this->xml;
		$values = array(); 
		$index  = array(); 
		$array  = array(); 
		$parser = xml_parser_create(); 
		xml_parser_set_option($parser, XML_OPTION_SKIP_WHITE, 1);
		xml_parser_set_option($parser, XML_OPTION_CASE_FOLDING, 0);
		xml_parse_into_struct($parser, $xml, $values, $index);
		xml_parser_free($parser);
		$i = 0; 
		$name = $values[$i]['tag']; 
		$array[$name] = isset($values[$i]['attributes']) ? $values[$i]['attributes'] : ''; 
		$array[$name] = $this->_struct_to_array($values, $i); 
		return $array; 
	}//createArray
}