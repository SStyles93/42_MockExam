/* Test harness: compiled together with the submitted ft_strlen.c
 * (and with the reference). Prints ft_strlen() of each argument. */
#include <stdio.h>

int	ft_strlen(char *str);

int	main(int argc, char **argv)
{
	int	i;

	i = 1;
	while (i < argc)
	{
		printf("%d\n", ft_strlen(argv[i]));
		i++;
	}
	return (0);
}
