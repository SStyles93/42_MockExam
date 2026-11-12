#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct s_point
{
	int	x;
	int	y;
}	t_point;

void	flood_fill(char **tab, t_point size, t_point begin);

/* usage: ./a.out begin_x begin_y row1 row2 ... */
int	main(int argc, char **argv)
{
	t_point	size;
	t_point	begin;
	char	**tab;
	int		i;

	if (argc < 4)
		return (0);
	begin.x = atoi(argv[1]);
	begin.y = atoi(argv[2]);
	size.y = argc - 3;
	size.x = strlen(argv[3]);
	tab = malloc(sizeof(char *) * size.y);
	i = 0;
	while (i < size.y)
	{
		tab[i] = strdup(argv[3 + i]);
		i++;
	}
	flood_fill(tab, size, begin);
	i = 0;
	while (i < size.y)
	{
		printf("%s\n", tab[i]);
		free(tab[i++]);
	}
	free(tab);
	return (0);
}
