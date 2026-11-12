#include <stdio.h>
#include <stdlib.h>

unsigned char	reverse_bits(unsigned char octet);

int	main(int argc, char **argv)
{
	int	i;

	i = 1;
	while (i < argc)
	{
		printf("%u\n", (unsigned int)reverse_bits((unsigned char)atoi(argv[i])));
		i++;
	}
	return (0);
}
