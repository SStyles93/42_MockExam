#include <stdio.h>
#include <stdlib.h>

int	*ft_rrange(int start, int end);

int	main(int argc, char **argv)
{
	int	*tab;
	int	start;
	int	end;
	int	len;
	int	i;

	if (argc != 3)
		return (0);
	start = atoi(argv[1]);
	end = atoi(argv[2]);
	len = (end > start ? end - start : start - end) + 1;
	tab = ft_rrange(start, end);
	if (!tab)
	{
		printf("NULL\n");
		return (0);
	}
	i = 0;
	while (i < len)
		printf("%d ", tab[i++]);
	printf("\n");
	free(tab);
	return (0);
}
