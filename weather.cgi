#!/usr/bin/perl -w

use LWP::Simple;
use URI;
use strict;
use CGI qw(:standard);
use XML::Simple;
use Data::Dumper;
use lib '/home/jimsmithkka/perl/lib';
use tzid;

open ERR,">>/home/jimsmithkka/files/output.err";

#my %locations; 

my %notifications;
my $config="./weather_config_dump";
my $countyfile="./countycodes.csv";

my $q = CGI->new;
my $params=$q->Vars;
my $tzid = tzid->new(sessiondir => '/home/jimsmithkka/www/tzid-sessions');
my $user = $tzid->user();

sub loadConfig2  #replace with datadumper for now, later implement mysql
{
	open CONF, "</home/jimsmithkka/files/weather.conf";
	while (<CONF>)
	{
		chomp;
		my ($loc,$code,$em)=split /:/;
		$locations{"$loc:$code"}='';
		
		foreach my $email (split(/,/,$em))
		{
			if ($notifications{$code})
			{
				push (@{$notifications{$code}}, $email);
				print ERR ":second email:";
			}
			else
			{
				print ERR ":new email:";
				$notifications{$code}=["$email"];
			}
		}
	}
	close CONF;
}

sub loadConfig  #replace with datadumper for now, later implement mysql
{
	open my $conf2,"<",$_[0] or die "cannot open file for reading\n"; 
	my $pants;
	{
		undef $/;
		$pants= <$conf2>;
	}
	close $conf2;

	print "$pants \n";
	my %printable=%{eval $pants};

	print Dumper(\%printable);

	#my %printable=%{$RBuids};
	print "Asses\n ";
	foreach my $sid (keys %printable)
	{
		print "$sid:\n";
		foreach my $loc (keys %{$printable{$sid}})
		{
			print "$loc:";
			foreach  my $num (@{$printable{$sid}->{$loc}})
			{
				print "$num, ";
			}
			print "\n";
		}
	}
	return \%printable;

}
sub writeConfig  #replace with datadumper for now, later implement mysql
{
	open my $conf,">",$_[0] or die "cannot open file for writing\n";
	$Data::Dumper::Terse=1; #strip VAR1 from the dumped data
	print $conf Dumper($_[1]);
	close $conf;
}

sub getData					#connects to national weather servcie and grabs their data
{
	my %responses;
	my $LP_RSS="http://alerts.weather.gov/cap/wwaatmget.php?x=$_[0]";
	
	my $LP_Page = get $LP_RSS;
 	my $LP_warnings;# = "http://jimsmithkka.lt3.us/test_put.xml";

	if ( $LP_Page =~ /\"([^\"]*wwacapget[^\"]*)\"/) 
	{
		$LP_warnings = $1; 
	}
	die "you prick, no warnings" unless defined $LP_Page;

 	my $LP_WarnPage = get $LP_warnings;
	
	if (!$LP_WarnPage)
	{
		$responses{"all clear"}="No Warnings Currently";
		return \%responses;
	}

 	my $xml_ref=XMLin("$LP_WarnPage");#", ForceArray => 1);

	$responses{"description"}=$xml_ref->{'info'}{'description'};
	$responses{"note"}=$xml_ref->{'info'}{'note'};
	$responses{"event"}=$xml_ref->{'info'}{'event'};
	$responses{"severity"}=$xml_ref->{'info'}{'severity'};
	$responses{"certainty"}=$xml_ref->{'info'}{'certainty'};
	$responses{"effective"}=$xml_ref->{'info'}{'effective'};
	$responses{"expires"}=$xml_ref->{'info'}{'expires'};
	$responses{"headline"}=$xml_ref->{'info'}{'headline'};
	$responses{"area"}=$xml_ref->{'info'}{'area'}{'areaDesc'};
	$responses{"urgency"}=$xml_ref->{'info'}{'urgency'};
	$responses{"instruction"}=$xml_ref->{'info'}{'instruction'};
	
	return \%responses;
}
sub printINPUT				#Handles input form
{
	unless ($user)
	{
		my $url=$tzid->url("login");
		print "<div id=login><a href=$url>Login</a></div>";
		return ;
	}

	print '<div id="formed">';
		print start_form(-name=>"fillout");
		
		print "<h5>Enter new location information here (still in alpha)</h5>";	
		print '<div id="email"><p>Your email address you wish to receive alerts for this locaiton on:';
 		print textfield('email_input','you@some.place',50,80);
 		print '</p></div>';
		
 		print '<div id="location"><p>Location: ';			
 		print textfield('location_name','Somewhere, SP',50,80);
 		print '</p></div>';
	
 		print '<div id="code"><p>Location Code (codes can be found <a href="http://alerts.weather.gov/">Here</a>):<br>';
 		print textfield('code_input','SPC001',50,80);	
 		print '</p></div>';

		print '<div id="button">'; 		#buttons on form
		print submit('Add to Config'); 	#run and make changes
		print defaults('Reset');	#set the form to defaults
		print '</div>';
		print end_form;
	print '</div>';	

	print "<HR><HR>";
}
sub picard
{
	print ERR ":adding email:";
	my $email=$params->{'email'}; 
	my $loc=$params->{'location'};	
	my $code=$params->{'code_input'};
	open my $wconf,">>./files/weather.conf";
	if ($notifications{$code})
	{
		print $wconf "$loc:$code:$email,";
		foreach my $oemail (@{$notifications{$code}})
		{
			print $wconf "$oemail,";
		}
		print $wconf "\n";
	}
	else
	{		
		print $wconf "$loc:$code:$email,\n";
	}	
	close $wconf;
}

sub loadCounties
{
	my %locations;
	open $county,"<",$countyfile;
	foreach my $line (<$county>)
	{
		@liner=split(/\,/,$line);
		$location{$liner[3] . $liner[4] . $liner[5]}=$liner[1] .  ", " . $liner[3];
	}
	return \%locations;
}
sub locationList
{
	my %ids=%{$_[0]};
	my %locs;
	my $codes=loadCounties;
	
	foreach my $id (keys %ids)
	{
		foreach my $loc (keys %{$ids{$id}})
		{
			$locs{$codes->{$loc}}=$loc;
		}
	}
	return \%locs;
}
sub main
{	
	print ERR ":Reading config files:";
	my %ids=%{loadConfig($config)};			#load user IDs, locations, and contacts
	my %locations=locationList(\%ids);		#map County, State to County codes for only the codes found in config (not all 3k us counties)
	print ERR ":End config files:";
	
	print $q->header(-type  =>  'text/html');
	print $q->start_html(-title=>'Weather Warning 2.0', -style=>{-media => 'all'});	# start the HTML
	print '<body style=background-color:black><pre style=color:white>';
	
	print ERR ":Writing Input to page:";
	printINPUT;
	print ERR ":End Input:";
	
	if ($params->{'email'})
	{
		if ($params->{'email'} ne 'you@some.place') 
		{
			print ERR ":Adding email step1:";
			picard;
			print ERR ":End Adding:";
		}		
	}


	foreach my $local (sort (keys %locations))
	{
		print ERR ":Start Display:";
		my ($loc, $code, $email)=split /:/, $local;
		$locations{$local}=&getData($code);
		print "<br><div id=$code>";
		print "<h3>$loc ($code)</h3>";
		foreach my $sect (keys %{$locations{$local}})
		{
			my $stuff=$locations{$local}->{$sect};
			print "$stuff<br>" if ($stuff);
		
		}
		print "</div>";
		print "<HR>";
		print ERR ":End Display:";
	}

	print $q->end_html;
}

main;
close ERR;