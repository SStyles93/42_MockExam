#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <errno.h>

#define MAX_CITIES 11

/* Distance between two cities. */
static float	distance(float a[2], float b[2])
{
	return (sqrtf((b[0] - a[0]) * (b[0] - a[0]) + (b[1] - a[1]) * (b[1] - a[1])));
}

static void	search(float d[MAX_CITIES][MAX_CITIES], int count, int *used, int last,
				int visited, float length, float *best)
{
	int	i;

	if (length >= *best)
		return ;
	if (visited == count)
	{
		if (length + d[last][0] < *best)
			*best = length + d[last][0];
		return ;
	}
	i = 1;
	while (i < count)
	{
		if (!used[i])
		{
			used[i] = 1;
			search(d, count, used, i, visited + 1, length + d[last][i], best);
			used[i] = 0;
		}
		i++;
	}
}

/* Returns the length of the shortest closed path visiting all the cities. */
static float	tsp(float (*cities)[2], int count)
{
	float	d[MAX_CITIES][MAX_CITIES];
	int		used[MAX_CITIES];
	float	best;
	int		i;
	int		j;

	if (count < 2)
		return (0);
	i = -1;
	while (++i < count)
	{
		used[i] = 0;
		j = -1;
		while (++j < count)
			d[i][j] = distance(cities[i], cities[j]);
	}
	best = 1e30f;
	search(d, count, used, 0, 1, 0.0f, &best);
	return (best);
}

/* Reads "x, y" lines from stdin into cities. Returns the number of cities,
 * or -1 on error. */
static int	read_cities(float (*cities)[2])
{
	int	count;
	int	ret;

	count = 0;
	while (count < MAX_CITIES)
	{
		ret = fscanf(stdin, "%f, %f\n", &cities[count][0], &cities[count][1]);
		if (ret != 2)
			break ;
		count++;
	}
	if (ferror(stdin))
		return (-1);
	return (count);
}

int	main(void)
{
	float	cities[MAX_CITIES][2];
	int		count;

	count = read_cities(cities);
	if (count < 0)
	{
		fprintf(stderr, "Error: could not read the input\n");
		return (1);
	}
	fprintf(stdout, "%.2f\n", tsp(cities, count));
	return (0);
}
