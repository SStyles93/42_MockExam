#include <stdio.h>
#include <stdlib.h>

void	sort_int_tab(int *tab, unsigned int size);

int	main(int argc, char **argv)
{
	int	*tab;
	int	i;

	tab = malloc(sizeof(int) * argc);
	i = 1;
	while (i < argc)
	{
		tab[i - 1] = atoi(argv[i]);
		i++;
	}
	sort_int_tab(tab, argc - 1);
	i = 0;
	while (i < argc - 1)
		printf("%d ", tab[i++]);
	printf("\n");
	free(tab);
	return (0);
}
