#!/usr/bin/perl -w

use Data::Dumper;
use strict;
my %uids;
my $id="null";
my $file="./weather_config_dump";
my $no=0;

if ($ARGV[0]) #for only reading back, call script with the word "no"
{
	$id=$ARGV[0];
	$no=1;
}

while ($id ne "no")
{
	my $loc="null";
	my %locs;
	print "Enter a UID ('no' to exit): ";
	$id=<STDIN>;
	chomp $id;
	if (($id eq "no") or $id eq "null")
	{
		next;
	}
	while ($loc ne "no")
	{
		my $num="555-555-5555";
		my @nums;
		print "Enter a Location ('no' to exit): ";
		$loc=<STDIN>;
		chomp $loc;
		if (($loc eq "null") or ($loc eq "no"))
		{
			next;
		}
		while ($num ne "no")
		{
			print "Enter a Number ('no' to exit): ";
			$num=<STDIN>;
			chomp $num;
			if (($num eq "555-555-5555") or ($num eq "no"))
			{
				next;
			}
			print "$num \n";
			push(@nums,$num);
		}
		print "$loc \n";
		$locs{$loc}=\@nums;
	}
	print "$id \n";
	$uids{$id}=\%locs;
} 

if ($no != 1)
{
	open my $conf,">","$file" or die "cannot open file for writing\n";
	$Data::Dumper::Terse=1; #strip VAR1 from the dumped data
	print $conf Dumper(\%uids);
	close $conf;
}

print "Heres your config written to $file : \n";



open my $conf2,"<","./weather_config_dump" or die "cannot open file for reading\n"; 
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

