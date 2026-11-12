#include <stdio.h>
#include <stdlib.h>

void	ft_swap(int *a, int *b);

int	main(int argc, char **argv)
{
	int	a;
	int	b;
	int	i;

	i = 1;
	while (i + 1 < argc)
	{
		a = atoi(argv[i]);
		b = atoi(argv[i + 1]);
		ft_swap(&a, &b);
		printf("a=%d b=%d\n", a, b);
		i += 2;
	}
	return (0);
}
