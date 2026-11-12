#include <stdio.h>
#include <stdlib.h>

static void	print_subset(int *set, int n, long mask)
{
	int	i;
	int	first;

	first = 1;
	i = 0;
	while (i < n)
	{
		if (mask & (1L << i))
		{
			if (!first)
				printf(" ");
			printf("%d", set[i]);
			first = 0;
		}
		i++;
	}
	printf("\n");
}

int	main(int argc, char **argv)
{
	int		*set;
	int		target;
	int		n;
	int		i;
	long	mask;
	long	sum;

	if (argc < 2)
		return (1);
	target = atoi(argv[1]);
	n = argc - 2;
	set = malloc(sizeof(int) * (n + 1));
	if (!set)
		return (1);
	i = -1;
	while (++i < n)
		set[i] = atoi(argv[i + 2]);
	mask = 0;
	while (mask < (1L << n))
	{
		sum = 0;
		i = -1;
		while (++i < n)
			if (mask & (1L << i))
				sum += set[i];
		if (sum == target)
			print_subset(set, n, mask);
		mask++;
	}
	free(set);
	return (0);
}
