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

/* Returns the length of the shortest closed path visiting all the cities.
 * write your code here */
static float	tsp(float (*cities)[2], int count)
{
	(void)cities;
	(void)count;
	(void)distance;
	return (0);
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
