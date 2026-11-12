#include <stdlib.h>

char	*ft_itoa(int nbr)
{
	long	n;
	int		len;
	char	*s;

	n = nbr;
	len = (n <= 0);
	while (n)
	{
		n /= 10;
		len++;
	}
	s = malloc(len + 1);
	if (!s)
		return (NULL);
	s[len] = '\0';
	n = nbr;
	if (n < 0)
	{
		s[0] = '-';
		n = -n;
	}
	if (n == 0)
		s[0] = '0';
	while (n)
	{
		s[--len] = '0' + n % 10;
		n /= 10;
	}
	return (s);
}
