package packgername

func fib(n int) int{
    if n <= 0 {
        return 0
    }else if n==1 {
        return 1
    }
    return fib(n-1) + fib(n-2)
}

func main() int {
    var n int=6
    var x int
    x = fib(n)
    return x
}