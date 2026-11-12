#include <stdio.h>
#include <stdlib.h>

int	main(int argc, char **argv)
{
	int	n;
	int	f;
	int	first;

	if (argc == 2)
	{
		n = atoi(argv[1]);
		if (n == 1)
			printf("1");
		f = 2;
		first = 1;
		while (n > 1)
		{
			if (n % f == 0)
			{
				if (!first)
					printf("*");
				printf("%d", f);
				first = 0;
				n /= f;
			}
			else
				f++;
		}
	}
	printf("\n");
	return (0);
}
